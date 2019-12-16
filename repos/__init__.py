from github import Github, GithubException
from github.Repository import Repository
from github.Organization import Organization
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset
import requests
import io
import os


def get_organization(git: Github):
    return git.get_organization("converge-app")


def get_repos(org: Organization):
    return org.get_repos()


def get_releases(repos: [Repository]):
    releases = []
    for repo in repos:
        latest_release = get_latest_release(repo)
        if latest_release == None:
            continue
        releases.append(latest_release)

    return releases


def get_latest_release(repo: Repository):
    print("getting: " + repo.name)
    try:
        release = repo.get_latest_release()
        print("  found")
        return release
    except GithubException as e:
        print("  not found")


def get_zip_and_documents(releases: [GitRelease]):
    zip_urls = []
    assets = []

    for release in releases:
        zip_urls.append(release.zipball_url)
        assets.append(get_assets(release))

    flat_assets = []
    for asset in assets:
        for a in asset:
            flat_assets.append(a)

    for zip_url in zip_urls:
        flat_assets.append({
            'type': 'zip_ball',
            'url': zip_url,
            'name': zip_url.split('/')[-3] + '.zip'
        })
    return flat_assets


def get_asset(asset: GitReleaseAsset):
    return {
        'type': 'asset',
        'url': asset.browser_download_url,
        'name': asset.browser_download_url.split('/')[-1]
    }


def get_assets(release: GitRelease):
    try:
        assets = release.get_assets()
        downloadables = []
        for asset in assets:
            downloadables.append(get_asset(asset))
        return downloadables
    except GithubException as e:
        print("    No assets found")


def get_source(assets):
    return [a for a in assets if a['type'] == 'zip_ball']


def get_documents(assets):
    return [a for a in assets if a['type'] == 'asset']


def save_documents(documents):
    for document in documents:
        r = requests.get(document['url'])
        f = open(os.path.join('.', 'out', 'documents', document['name']), 'wb')
        f.write(r.content)


def save_source(files):
    for file in files:
        r = requests.get(file['url'])
        f = open(os.path.join('.', 'out', 'source', file['name']), 'wb')
        f.write(r.content)


def bake():
    import zipfile
    zf = zipfile.ZipFile("converge-project.zip", "w")
    for dirname, subdirs, files in os.walk("./out"):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()
