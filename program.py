import do_not_share
import repos


def main():
    git = do_not_share.initialize()
    org = repos.get_organization(git)
    repositories = repos.get_repos(org)
    releases = repos.get_releases(repositories)
    assets = repos.get_zip_and_documents(releases)
    source = repos.get_source(assets)
    documents = repos.get_documents(assets)
    repos.save_documents(documents)
    repos.save_source(source)
    repos.bake()


if __name__ == "__main__":
    main()
