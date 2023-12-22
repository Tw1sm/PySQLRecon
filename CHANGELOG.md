# Changelog
## [v0.1.2] - 09/21/2023
### Fixed
- Issue #1
- When using `clr` module, if custom assembly already exists under a different name `pysqlrecon` would previously log the error and exit
    - Now it deletes the offending assembly and tries creation again

## [v0.1.1] - 09/03/2023
- Initial commit