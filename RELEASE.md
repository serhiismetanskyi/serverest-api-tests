## Release Notes

### 0.1.0 – Initial Version

**Overview**
- First version of the automated test suite for the ServeRest API.

**Features**
- Added pytest-based tests for users, products, carts and login endpoints.
- Implemented data-driven tests with Faker and reusable fixtures.

**Observability**
- Implemented custom HTTP logging to files and HTML reports (pytest-html).

**Infrastructure**
- Docker containerization with Docker Compose for isolated test execution environment.
