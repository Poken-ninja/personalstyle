"""Current-account local boundary. No product records or credentials are stored."""

import logging
import os
import stat
import subprocess
from pathlib import Path


class SecurityError(ValueError):
    """A local security precondition was not met."""

    def __init__(
        self, message: str, *, phase: str = "path_validation",
        phase_detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.phase = phase
        self.phase_detail = (
            phase_detail if phase_detail in SECURITY_PHASE_DETAILS else None
        )


SECURITY_PHASES = frozenset({
    "platform_check",
    "path_validation",
    "directory_presence_check",
    "directory_create",
    "directory_acl_apply",
    "directory_acl_verify",
    "file_create",
    "file_metadata_check",
    "file_acl_apply",
    "file_acl_verify",
})
SECURITY_PHASE_DETAILS = frozenset({
    "acl_unprotected", "acl_owner_mismatch", "acl_rule_count_mismatch",
    "acl_identity_rule_mismatch", "acl_rule_attributes_mismatch",
    "acl_process_start_failed", "acl_process_timeout", "acl_command_failed",
})


def log_event(logger: logging.Logger, event: str, count: int = 0) -> None:
    """Emit only fixed identifiers and bounded counters, never caller text."""
    if event not in {"startup_valid", "startup_rejected", "storage_prepared"}:
        raise SecurityError("Unsupported telemetry event")
    if type(count) is not int or not 0 <= count <= 1_000_000:
        raise SecurityError("Invalid telemetry counter")
    logger.info("event=%s count=%d", event, count)


# Path is passed through an environment variable, not interpolated into PowerShell.
# Windows supplies the account SID; no client identity or credential is accepted.
ACL_CONTEXT = r"""
$ErrorActionPreference = 'Stop'
$target = [Environment]::GetEnvironmentVariable('PERSONALSTYLE_SECURE_PATH')
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
$system = [Security.Principal.SecurityIdentifier]::new('S-1-5-18')
$inherit = [Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit'
"""
ACL_CREATE = r"""
$acl = [Security.AccessControl.DirectorySecurity]::new()
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true, $false)
foreach ($identity in @($sid, $system)) {
    $rule = [Security.AccessControl.FileSystemAccessRule]::new(
        $identity, 'FullControl', $inherit, 'None', 'Allow')
    $acl.AddAccessRule($rule)
}
Set-Acl -LiteralPath $target -AclObject $acl
"""
ACL_VERIFY = r"""
$acl = Get-Acl -LiteralPath $target
if (-not $acl.AreAccessRulesProtected) {
    [Console]::Out.WriteLine('PSTYLE_DIAG:acl_unprotected'); exit 21
}
if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid.Value) {
    [Console]::Out.WriteLine('PSTYLE_DIAG:acl_owner_mismatch'); exit 22
}
$rules = $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 2) {
    [Console]::Out.WriteLine('PSTYLE_DIAG:acl_rule_count_mismatch'); exit 23
}
foreach ($identity in @($sid, $system)) {
    $matching = @($rules | Where-Object { $_.IdentityReference.Value -eq $identity.Value })
    if ($matching.Count -ne 1) {
        [Console]::Out.WriteLine('PSTYLE_DIAG:acl_identity_rule_mismatch'); exit 24
    }
    $rule = $matching[0]
    if ($rule.IsInherited -or $rule.AccessControlType -ne 'Allow' -or
        $rule.FileSystemRights -ne 'FullControl' -or $rule.InheritanceFlags -ne $inherit -or
        $rule.PropagationFlags -ne 'None') {
        [Console]::Out.WriteLine('PSTYLE_DIAG:acl_rule_attributes_mismatch'); exit 25
    }
}
"""


def _check_path(path: Path) -> Path:
    if os.name != "nt":
        raise SecurityError(
            "Private storage preparation is verified only on Windows",
            phase="platform_check",
        )
    absolute = path.absolute()
    if ".." in absolute.parts or absolute == Path(absolute.anchor):
        raise SecurityError("Invalid profile directory", phase="path_validation")
    try:
        for ancestor in (absolute, *absolute.parents):
            if ancestor.exists() or ancestor.is_symlink():
                attributes = ancestor.lstat().st_file_attributes
                if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    raise SecurityError("Reparse paths are not allowed", phase="path_validation")
    except OSError as error:
        raise SecurityError("Profile path cannot be inspected", phase="path_validation") from error
    return absolute


def _acl(path: Path, create: bool = False, file: bool = False) -> None:
    # PS7 -> Python -> Windows PowerShell otherwise inherits incompatible PS7 modules.
    environment = {key: value for key, value in os.environ.items() if key.upper() != "PSMODULEPATH"}
    environment["PERSONALSTYLE_SECURE_PATH"] = str(path)
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    context = ACL_CONTEXT
    creation = ACL_CREATE
    object_name = "file" if file else "directory"
    action_name = "apply" if create else "verify"
    phase = f"{object_name}_acl_{action_name}"
    if file:
        context += "\n$inherit = [Security.AccessControl.InheritanceFlags]::None\n"
        creation = creation.replace("DirectorySecurity", "FileSecurity")
    script = "try {\n" + context + (creation if create else "") + ACL_VERIFY + "\n} catch { [Console]::Out.WriteLine('PSTYLE_DIAG:acl_command_failed'); exit 31 }"
    try:
        result = subprocess.run(
            [str(powershell), "-NoProfile", "-NonInteractive", "-Command", script],
            env=environment, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=10, check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise SecurityError(
            "OS permission verification unavailable", phase=phase,
            phase_detail="acl_process_timeout",
        ) from error
    except OSError as error:
        raise SecurityError(
            "OS permission verification unavailable", phase=phase,
            phase_detail="acl_process_start_failed",
        ) from error
    if result.returncode != 0:
        # Never echo subprocess output containing paths or account information.
        safe_markers = {"PSTYLE_DIAG:" + item for item in SECURITY_PHASE_DETAILS}
        detail = next(
            (line.removeprefix("PSTYLE_DIAG:") for line in result.stdout.splitlines()
             if line in safe_markers),
            "acl_command_failed",
        )
        raise SecurityError(
            "Private profile permissions could not be verified", phase=phase,
            phase_detail=detail,
        )


def verify_private_directory(path: Path) -> None:
    """Read back OS ownership and ACL before any future engine write."""
    absolute = _check_path(path)
    if not absolute.is_dir():
        raise SecurityError("Profile directory is unavailable", phase="directory_presence_check")
    _acl(absolute)


def prepare_private_directory(path: Path) -> Path:
    """Prepare an empty directory, refusing to take over existing user data."""
    absolute = _check_path(path)
    try:
        if absolute.exists():
            if not absolute.is_dir() or any(absolute.iterdir()):
                raise SecurityError("Existing profile directory is not empty", phase="directory_create")
            verify_private_directory(absolute)
        else:
            # Parent must already exist; never recursively take over ancestors.
            absolute.mkdir()
            _acl(absolute, create=True)
    except OSError as error:
        raise SecurityError("Profile directory preparation failed", phase="directory_create") from error
    return absolute


def verify_private_file(path: Path) -> None:
    """Verify an explicitly protected canonical file, rejecting links/replacements."""
    absolute = _check_path(path)
    try:
        info = absolute.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SecurityError("Invalid private file", phase="file_metadata_check")
    except OSError as error:
        raise SecurityError("Private file is unavailable", phase="file_metadata_check") from error
    _acl(absolute, file=True)


def prepare_private_file(path: Path) -> None:
    """Create only a new empty file inside a verified directory; never take over files."""
    absolute = _check_path(path)
    verify_private_directory(absolute.parent)
    try:
        with absolute.open("xb"):
            pass
    except OSError as error:
        raise SecurityError("Private file creation failed", phase="file_create") from error
    _acl(absolute, create=True, file=True)
    verify_private_directory(absolute.parent)
    verify_private_file(absolute)
