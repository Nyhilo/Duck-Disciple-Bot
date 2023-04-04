import core.db.settings_db as db


class Settings():
    @property
    def current_locale_key(self):
        return db.get_setting('current_locale_key')

    @current_locale_key.setter
    def current_locale_key(self, value):
        db.save_setting('current_locale_key', value)


# Module-level constant for easy importing
settings = Settings()
