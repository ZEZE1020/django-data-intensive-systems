# Test Strategy

## Quality objectives

The suite protects API correctness, data access policies, tenant isolation, and operational behavior. Tests are written as executable acceptance criteria, with negative cases treated as first-class scenarios.

## Test layers

- **Unit tests:** Validate model behavior, serializers, validators, and small deterministic utilities without external services.
- **Integration tests:** Exercise Django views, authentication, database transactions, middleware, and Celery boundaries together.
- **API contract validation:** DRF tests assert HTTP status codes, response shape, validation errors, authentication requirements, boundary values, and that invalid writes do not mutate data.
- **Access policy tests:** Every tenant-aware endpoint includes a cross-tenant denial case. These tests are explicitly **Validating data access policies and isolation rules.**

## CI/CD automation

GitHub Actions runs on pushes and pull requests targeting `main`. It installs the pinned development requirements, runs `flake8`, builds the Compose web image, and executes `pytest -v` inside the Compose environment. A local failure should be reproducible with the same command used by reviewers. CodeQL runs separately for static analysis.

The QA evidence workflow runs on `main`, on a schedule, or by manual dispatch. It publishes JUnit results, HTML coverage, Locust CSV/HTML output, and profiling output as a GitHub Pages artifact. PRs use the fast quality gate; longer load tests do not delay every code review.

## API contract and evidence

OpenAPI is generated with `drf-spectacular` and served through Swagger UI and ReDoc. Schema generation is a CI-checkable contract surface. The evidence dashboard links the generated API and performance artifacts so a reviewer can inspect both the quality philosophy and its practical results.

## Load testing

Locust scenarios live in `scripts/load_test.py` and run against the Compose `web` service. Each simulated user owns a tenant and uses the public API paths. Load tests are kept separate from the per-commit suite because they require a running stack and produce operational metrics such as throughput, latency percentiles, and error rate. They can be run headlessly in a performance environment before release.

## Defect workflow

Failures become bug tickets containing reproduction steps, expected and actual behavior, environment details, logs, and an acceptance criterion tied to a regression test.

## Deliberate future scope

Distributed tracing, queue-depth metrics, database partitioning, and payment retry orchestration require separate design decisions and operational acceptance criteria. They are tracked as future work rather than being enabled without corresponding tests and service ownership.