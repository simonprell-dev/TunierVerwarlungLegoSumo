from app.application.commands.get_version_command import GetVersionCommand


class VersionService:
    def execute(self, command: GetVersionCommand) -> dict[str, str]:
        return {
            "service": command.service,
            "version": command.version,
            "api_version": command.api_version,
        }
