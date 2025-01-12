# Changelog
## [v0.3.1] - 1/11/2024
### Added
- Added a query to check the `ExtendedProtection` registry value in the Info module

## [v0.3.0] - 08/05/2024
### Added
- SCCM modules from [SQLRecon](https://github.com/skahwah/SQLRecon?tab=readme-ov-file#sccm-modules)
    - `addadmin`
    - `credentials`
    - `logons`
    - `removeadmin`
    - `sites`
    - `taskdata`
    - `tasklist`
    - `users`

## [v0.2.1] - 07/26/2024
### Fixed
- Issue [#12](https://github.com/Tw1sm/PySQLRecon/issues/12)

## [v0.2.0] - 06/26/2024
### Added
- `sample` module to retrive table data without manual SQL query

## [v0.1.4] - 02/03/2024
### Fixed
- Issue [#9](https://github.com/Tw1sm/PySQLRecon/issues/9)
- `search`, `columns` and `rows` modules now appropriately use linked rpc queries - these modules would previously fail

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