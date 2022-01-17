import os

class Config:

    def __init__(self):
        self._sonar_url = os.environ['SONAR_URL']
        self._sonar_user = os.environ['SONAR_USER']
        self._sonar_password = os.environ['SONAR_PASSWORD']

    @property
    def sonar_url(self):
        return self._sonar_url

    @property
    def sonar_user(self):
        return self._sonar_user

    @property
    def sonar_password(self):
        return self._sonar_password

    @property
    def supported_keys(self):
        return SUPPORTED_KEYS

SUPPORTED_KEYS = [
    {
        "domain" : "Reliability",
        "keys" : [
            "bugs",
            "reliability_rating"
        ]
    },
    {
        "domain" : "Security",
        "keys" : [
            "vulnerabilities",
            "security_rating",
            "security_review_rating"
        ]
    },
    {
        "domain" : "Maintainability",
        "keys" : [
            "code_smells",
            "sqale_rating",
            "sqale_index",
            "sqale_debt_ratio"
        ]
    },
    {
        "domain" : "Duplications",
        "keys" : [
            "duplicated_blocks",
            "duplicated_files",
            "duplicated_lines",
            "duplicated_lines_density",
            "duplications_data"
        ]
    },
    {
        "domain" : "Coverage",
        "keys" : [
            "branch_coverage",
            "executable_lines_data",
            "line_coverage",
            "lines_to_cover"
        ]
    },
    {
        "domain" : "Size",
        "keys" : [
            "comment_lines",
            "comment_lines_data",
            "comment_lines_density",
            "generated_lines",
            "generated_ncloc",
            "lines",
            "ncloc",
            "ncloc_data",
            "ncloc_language_distribution",
            "projects",
            "statements"
        ]
    },
    {
        "domain" : "Issues",
        "keys" : [
            "open_issues",
            "reopened_issues",
            "confirmed_issues"
        ]
    }
]