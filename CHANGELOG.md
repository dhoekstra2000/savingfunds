# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.3.1 - 2024-03-09

### Fixed
- Bug in fixing underdistribution of sub fundgroups when using the monthly distribution mode.

## 0.3.0 - 2024-03-08

### Added
- Flag to withdraw command to simultaneously lower the target.

### Changed
- Reporting of distributions now shows account comments and IBAN only if it is set.

### Fixed
- Make the distribution commands ensure proper arithmetic for money, to avoid stray cents.

## 0.2.0 - 2024-02-07

### Added

- Command to list details of an account.
- Tracking of IBAN and comments of an account.
- Command to change IBAN of an account.
- Command to change the comments of an account.
- Add IBAN to reporting commands.

## 0.1.1 - 2024-02-01

### Fixed

- Extra distribution now takes into account that funds can be filled completely.
