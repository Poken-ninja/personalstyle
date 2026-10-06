"""Current-account local boundary. No product records or credentials are stored."""

import logging
import os
import stat
import subprocess
from pathlib import Path


class SecurityError(ValueError):
    """A local security precondition was not met."""


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
if (-not $acl.AreAccessRulesProtected) { throw 'Unprotected ACL' }
if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne $sid.Value) {
    throw 'Wrong owner'
}
$rules = $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 2) { throw 'Unexpected ACL rules' }
foreach ($identity in @($sid, $system)) {
    $matching = @($rules | Where-Object { $_.IdentityReference.Value -eq $identity.Value })
    if ($matching.Count -ne 1) { throw 'Wrong identity' }
    $rule = $matching[0]
    if ($rule.IsInherited -or $rule.AccessControlType -ne 'Allow' -or
        $rule.FileSystemRights -ne 'FullControl' -or $rule.InheritanceFlags -ne $inherit -or
        $rule.PropagationFlags -ne 'None') { throw 'Unexpected permissions' }
}
"""


def _check_path(path: Path) -> Path:
    if os.name != "nt":
        raise SecurityError("Private storage preparation is verified only on Windows")
    absolute = path.absolute()
    if ".." in absolute.parts or absolute == Path(absolute.anchor):
        raise SecurityError("Invalid profile directory")
    try:
        for ancestor in (absolute, *absolute.parents):
            if ancestor.exists() or ancestor.is_symlink():
                attributes = ancestor.lstat().st_file_attributes
                if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    raise SecurityError("Reparse paths are not allowed")
    except OSError as error:
        raise SecurityError("Profile path cannot be inspected") from error
    return absolute


def _acl(path: Path, create: bool = False) -> None:
    environment = os.environ.copy()
    environment["PERSONALSTYLE_SECURE_PATH"] = str(path)
    powershell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / (
        "System32/WindowsPowerShell/v1.0/powershell.exe"
    )
    script = ACL_CONTEXT + (ACL_CREATE if create else "") + ACL_VERIFY
    try:
        result = subprocess.run(
            [str(powershell), "-NoProfile", "-NonInteractive", "-Command", script],
            env=environment, capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SecurityError("OS permission verification unavailable") from error
    if result.returncode != 0:
        # Never echo subprocess output containing paths or account information.
        raise SecurityError("Private profile permissions could not be verified")


def verify_private_directory(path: Path) -> None:
    """Read back OS ownership and ACL before any future engine write."""
    absolute = _check_path(path)
    if not absolute.is_dir():
        raise SecurityError("Profile directory is unavailable")
    _acl(absolute)


def prepare_private_directory(path: Path) -> Path:
    """Prepare an empty directory, refusing to take over existing user data."""
    absolute = _check_path(path)
    try:
        if absolute.exists():
            if not absolute.is_dir() or any(absolute.iterdir()):
                raise SecurityError("Existing profile directory is not empty")
            verify_private_directory(absolute)
        else:
            # Parent must already exist; never recursively take over ancestors.
            absolute.mkdir()
            _acl(absolute, create=True)
    except OSError as error:
        raise SecurityError("Profile directory preparation failed") from error
    return absolute
