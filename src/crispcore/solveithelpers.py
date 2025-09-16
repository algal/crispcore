def _gh_ssh_from_gh_url(gh_repo_address:str ## GH URL or GH SSH address
                        ) -> str:
    "Given a GH URL or SSH remote address, returns a SSH remote address or None"
    import re
    pattern = r'https://github\.com/([^/]+)/([^/]+)(?:/.*)?'
    if gh_repo_address.startswith("git@github.com:"): return gh_repo_address
    elif match := re.match(pattern, gh_repo_address):
        user, repo = match.groups()
        return f'git@github.com:{user}/{repo}.git'
    else: return None


def pip_install(gh_address:str # GH URL or GH SSH address
                ) -> bool:     # True, on success
    """Pip installs from repo, using GITHUB_TOKEN if avail.

    gh_address: like git@github.com:username/reponame.git"""
    import subprocess,sys,os
    token = os.getenv('GITHUB_TOKEN')
    repo_url = gh_address.replace("git@github.com:", f"https://{token}@github.com/")
    r = subprocess.run([sys.executable, "-m", "pip", "install",
                        "--force-reinstall",
                        f"git+{repo_url}"], check=True, capture_output=True)
    if r.returncode != 0:
        print(f"Install faied with stderr:\n{r.stderr}",file=sys.stderr)
    else:
        print("Install succeeded")
    return (r.returncode == 0)
    
    
