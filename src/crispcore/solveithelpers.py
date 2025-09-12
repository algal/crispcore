def pip_install(gh_address:str # GH address of form git@github.com:username/reponame.git
                ):
    """Pip installs from repo, using GITHUB_TOKEN if avail

    gh_address: like git@github.com:username/reponame.git"""
    import subprocess,sys,os
    token = os.getenv('GITHUB_TOKEN')
    repo_url = gh_address.replace("git@github.com:", f"https://{token}@github.com/")
    r = subprocess.run([sys.executable, "-m", "pip", "install", f"git+{repo_url}"], check=True, capture_output=True)
    return r.exit_code
    
    
