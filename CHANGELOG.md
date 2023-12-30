# Changelog
## [v0.1.3] - 12/30/2023
### Fixed
- Issue [#3](https://github.com/Tw1sm/PySQLRecon/issues/3)
- Roles queried from the database now use `IS_MEMBER` call instead `IS_SRVMEMBER` to check membership

## [v0.1.2] - 12/21/2023
### Fixed
- Issue [#1](https://github.com/Tw1sm/PySQLRecon/issues/1)
- When using `clr` module, if custom assembly already exists under a different name `pysqlrecon` would previously log the error and exit
    - Now it deletes the offending assembly and tries creation again

## [v0.1.1] - 09/03/2023
- Initial commit