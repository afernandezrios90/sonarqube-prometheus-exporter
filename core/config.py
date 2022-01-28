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
            "security_rating"
        ]
    },
    {
        "domain" : "Maintainability",
        "keys" : [
            "code_smells",
            "sqale_rating"
        ]
    },
    {
        "domain" : "Duplications",
        "keys" : []
    },
    {
        "domain" : "Coverage",
        "keys" : [
            "line_coverage"
        ]
    },
    {
        "domain" : "Size",
        "keys" : [
            "ncloc_language_distribution"
        ]
    },
    {
        "domain" : "Issues",
        "keys" : []
    }
]