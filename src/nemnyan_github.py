import settings

from github import Github


class NemnyanGithub:
    gh = Github(settings.GITHUB_TOKEN)
    repo = gh.get_repo('muro1214/Valheim_Nemnyan_Server')


    def get_latest_release_tag(self):
        release = self.repo.get_latest_release()

        return release.tag_name


    def get_latest_release_url(self):
        release = self.repo.get_latest_release()

        return release.html_url
