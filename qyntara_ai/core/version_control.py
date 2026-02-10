"""
Version Control Integration for Qyntara AI.
Supports Git and Perforce metadata injection into exported assets.
"""
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VersionControlBridge:
    """
    Integrates with Git/Perforce to inject metadata into exported assets.
    """
    def __init__(self):
        self.vcs_type = None  # 'git', 'p4', or None
        self.project_root = None
        
    def detect_vcs(self, project_path):
        """
        Detect version control system in project directory.
        Returns: 'git', 'p4', or None
        """
        project_path = Path(project_path)
        
        # Check for Git
        git_dir = project_path / ".git"
        if git_dir.exists():
            self.vcs_type = "git"
            self.project_root = str(project_path)
            logger.info(f"Detected Git repository at {self.project_root}")
            return "git"
        
        # Check for Perforce
        p4_config = project_path / ".p4config"
        if p4_config.exists():
            self.vcs_type = "p4"
            self.project_root = str(project_path)
            logger.info(f"Detected Perforce workspace at {self.project_root}")
            return "p4"
        
        # Check parent directories (up to 5 levels)
        current = project_path
        for _ in range(5):
            current = current.parent
            if (current / ".git").exists():
                self.vcs_type = "git"
                self.project_root = str(current)
                return "git"
            if (current / ".p4config").exists():
                self.vcs_type = "p4"
                self.project_root = str(current)
                return "p4"
        
        logger.warning("No version control system detected")
        return None
    
    def get_current_revision(self):
        """
        Get current VCS revision/changelist.
        Returns: dict with 'revision', 'author', 'timestamp', 'branch'
        """
        if not self.vcs_type:
            return None
        
        try:
            if self.vcs_type == "git":
                return self._get_git_info()
            elif self.vcs_type == "p4":
                return self._get_p4_info()
        except Exception as e:
            logger.error(f"Failed to get VCS info: {e}")
            return None
    
    def _get_git_info(self):
        """Get Git repository information."""
        try:
            # Get commit hash
            revision = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                text=True
            ).strip()
            
            # Get author
            author = subprocess.check_output(
                ["git", "log", "-1", "--format=%an"],
                cwd=self.project_root,
                text=True
            ).strip()
            
            # Get timestamp
            timestamp = subprocess.check_output(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.project_root,
                text=True
            ).strip()
            
            # Get branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                text=True
            ).strip()
            
            return {
                "revision": revision[:8],  # Short hash
                "author": author,
                "timestamp": timestamp,
                "branch": branch
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e}")
            return None
    
    def _get_p4_info(self):
        """Get Perforce workspace information."""
        try:
            # Get current changelist
            output = subprocess.check_output(
                ["p4", "changes", "-m1", "#have"],
                cwd=self.project_root,
                text=True
            ).strip()
            
            # Parse: "Change 12345 on 2024/01/01 by user@workspace 'Description'"
            parts = output.split()
            revision = parts[1] if len(parts) > 1 else "unknown"
            
            # Get user
            user_info = subprocess.check_output(
                ["p4", "info"],
                cwd=self.project_root,
                text=True
            )
            author = "unknown"
            for line in user_info.split("\n"):
                if line.startswith("User name:"):
                    author = line.split(":", 1)[1].strip()
                    break
            
            return {
                "revision": revision,
                "author": author,
                "timestamp": " ".join(parts[3:5]) if len(parts) > 4 else "unknown",
                "branch": "main"  # P4 doesn't have branches in the same way
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Perforce command failed: {e}")
            return None
    
    def inject_metadata_usd(self, usd_file_path, metadata=None):
        """
        Inject VCS metadata into USD file as custom attributes.
        
        Args:
            usd_file_path: Path to USD file
            metadata: Optional dict with custom metadata. If None, uses get_current_revision()
        """
        if metadata is None:
            metadata = self.get_current_revision()
        
        if not metadata:
            logger.warning("No VCS metadata available to inject")
            return False
        
        try:
            from pxr import Usd, Sdf
            
            # Open USD stage
            stage = Usd.Stage.Open(usd_file_path)
            if not stage:
                logger.error(f"Failed to open USD file: {usd_file_path}")
                return False
            
            # Get root prim
            root = stage.GetPseudoRoot()
            
            # Add custom metadata
            root.SetCustomDataByKey("vcs_revision", metadata.get("revision", "unknown"))
            root.SetCustomDataByKey("vcs_author", metadata.get("author", "unknown"))
            root.SetCustomDataByKey("vcs_timestamp", metadata.get("timestamp", "unknown"))
            root.SetCustomDataByKey("vcs_branch", metadata.get("branch", "unknown"))
            root.SetCustomDataByKey("vcs_type", self.vcs_type or "none")
            
            # Save
            stage.Save()
            logger.info(f"Injected VCS metadata into {usd_file_path}")
            return True
            
        except ImportError:
            logger.error("USD Python bindings not available")
            return False
        except Exception as e:
            logger.error(f"Failed to inject USD metadata: {e}")
            return False
    
    def create_commit_hook(self, export_dir, auto_commit=False):
        """
        Create a post-export commit hook (optional).
        
        Args:
            export_dir: Directory containing exported assets
            auto_commit: If True, automatically commit exported files
        """
        if not self.vcs_type or not auto_commit:
            return False
        
        try:
            if self.vcs_type == "git":
                # Git add + commit
                subprocess.run(
                    ["git", "add", export_dir],
                    cwd=self.project_root,
                    check=True
                )
                subprocess.run(
                    ["git", "commit", "-m", f"Auto-export from Qyntara AI: {export_dir}"],
                    cwd=self.project_root,
                    check=True
                )
                logger.info(f"Auto-committed {export_dir} to Git")
                return True
                
            elif self.vcs_type == "p4":
                # P4 add + submit
                subprocess.run(
                    ["p4", "add", export_dir],
                    cwd=self.project_root,
                    check=True
                )
                subprocess.run(
                    ["p4", "submit", "-d", f"Auto-export from Qyntara AI: {export_dir}"],
                    cwd=self.project_root,
                    check=True
                )
                logger.info(f"Auto-submitted {export_dir} to Perforce")
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Commit hook failed: {e}")
            return False
