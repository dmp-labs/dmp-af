# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Note

For changelog entries prior to v0.14.6, see
the [original dbt-af repository](https://github.com/Toloka/dbt-af/blob/main/CHANGELOG.md).

<!--next-version-placeholder-->

## v0.19.0 (2026-10-18)

### Features

- Add Airflow 3.3.2 support ([#24](https://github.com/dmp-labs/dmp-af/pull/24),
  [`24f27d0`](https://github.com/dmp-labs/dmp-af/commit/24f27d0137aa64ef79ecb9816e71abd8817ce361))


## v0.18.0 (2026-08-05)

### Features

- Add Airflow 3.3.0 support ([#21](https://github.com/dmp-labs/dmp-af/pull/21),
  [`f22dc91`](https://github.com/dmp-labs/dmp-af/commit/f22dc9183c1b0b7005a3c068b9123ea5ac2e481e))


## v0.17.0 (2026-06-25)

### Documentation

- Add Python 3.13 to all documentation
  ([`c7b79ab`](https://github.com/dmp-labs/dmp-af/commit/c7b79abb38b1e1bb6ac26e9557ced8448842e042))

- Update links in README.md ([#15](https://github.com/dmp-labs/dmp-af/pull/15),
  [`b4bedca`](https://github.com/dmp-labs/dmp-af/commit/b4bedcaba1d7da227607905b54d93c8a18b68e88))

### Features

- Add Airflow 3.2.x support ([#18](https://github.com/dmp-labs/dmp-af/pull/18),
  [`6b352d1`](https://github.com/dmp-labs/dmp-af/commit/6b352d1fc79da47966bf9e834523d00e4ca45e3c))

- Add weekly auto-PR for new Airflow releases ([#19](https://github.com/dmp-labs/dmp-af/pull/19),
  [`0426344`](https://github.com/dmp-labs/dmp-af/commit/04263448d96638a208c35e4bc9f6a0d6675dd02a))


## v0.16.0 (2025-11-15)

### Bug Fixes

- Add Airflow 3.0.x compat for LazyDeserializedDAG
  ([`86bf470`](https://github.com/dmp-labs/dmp-af/commit/86bf470e8c5f85f59c7f807c97425a0e04ff9902))

- Add mypy and fix issues ([#13](https://github.com/dmp-labs/dmp-af/pull/13),
  [`4e25a5f`](https://github.com/dmp-labs/dmp-af/commit/4e25a5f7bffacce03f1eb1c743898bac5088dc8a))

### Documentation

- Fix broken links and Firebase deployment issues
  ([#10](https://github.com/dmp-labs/dmp-af/pull/10),
  [`f8c1534`](https://github.com/dmp-labs/dmp-af/commit/f8c15344dcb1f71db5884ed1bba3dccf3a6049a0))

### Features

- Add Airflow 3.1.3 and Python 3.13 support ([#11](https://github.com/dmp-labs/dmp-af/pull/11),
  [`cb41301`](https://github.com/dmp-labs/dmp-af/commit/cb413015d72503d73c945f01f8df0f80ffcdf8b6))


## v0.15.0 (2025-10-28)

### Chores

- Add pull request template
  ([`5702cde`](https://github.com/dmp-labs/dmp-af/commit/5702cde03a1a93e8739d8802e416ec2a29f5e5d4))

- Remove site_url
  ([`a752140`](https://github.com/dmp-labs/dmp-af/commit/a752140d93d470cb6531d149e6bbfeb33940fb46))

- Trigger docs deploy on new tags ([#8](https://github.com/dmp-labs/dmp-af/pull/8),
  [`d8bde88`](https://github.com/dmp-labs/dmp-af/commit/d8bde888a0fb68fd720348969194c8e86bedf986))

- Update changelog generation
  ([`7583f52`](https://github.com/dmp-labs/dmp-af/commit/7583f5223aed0d912a4a330ebb35e5e6095b66d6))

- Update CONTRIBUTING.md
  ([`1697f7c`](https://github.com/dmp-labs/dmp-af/commit/1697f7ca45a7260d5f06a1f19a8d5c0543b440d1))

### Continuous Integration

- Add semantic release ([#3](https://github.com/dmp-labs/dmp-af/pull/3),
  [`7798ca0`](https://github.com/dmp-labs/dmp-af/commit/7798ca027742a3951a14bb41a97cda21c8f80d50))

### Documentation

- Add airflow 3.0.6 to tested matrix in docs ([#9](https://github.com/dmp-labs/dmp-af/pull/9),
  [`ed7e54d`](https://github.com/dmp-labs/dmp-af/commit/ed7e54d310440e4981476d4bb1200dc1db0c8d3c))

### Features

- Add airflow 3.0.6 support ([#2](https://github.com/dmp-labs/dmp-af/pull/2),
  [`888bda5`](https://github.com/dmp-labs/dmp-af/commit/888bda50ba3e550e3d2a8f6cc08bb0d4afb978fe))

- Add docs deploy workflow ([#6](https://github.com/dmp-labs/dmp-af/pull/6),
  [`26ef2d6`](https://github.com/dmp-labs/dmp-af/commit/26ef2d602a588187007a07f384caa02394f2fed7))

- Use github app to make release
  ([`978db83`](https://github.com/dmp-labs/dmp-af/commit/978db8302547230a9106bb171ad8597bcb5238e7))
