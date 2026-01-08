# Roadmap

Future plans for FastAPI Clean Architecture.

## Short Term (v1.1.0)

**Target**: Q2 2024

### WebSocket Support

Real-time bidirectional communication:

- WebSocket endpoint foundation
- Authentication for WebSocket connections
- Message broadcasting
- Room/channel management
- Example chat implementation

**Use cases**: Chat apps, live notifications, real-time dashboards

### Two-Factor Authentication (2FA)

Enhanced security:

- TOTP-based 2FA (Google Authenticator, Authy)
- QR code generation for setup
- Backup codes
- 2FA enable/disable endpoints
- Integration with login flow

### Rate Limiting

Prevent abuse and DoS attacks:

- Request rate limiting middleware
- Configurable limits per endpoint
- IP-based and user-based limits
- Redis backend for distributed systems
- Custom limit responses

### API Versioning

Support multiple API versions:

- URL-based versioning (`/api/v1/`, `/api/v2/`)
- Version deprecation warnings
- Version-specific documentation
- Migration guides between versions

## Medium Term (v1.2.0)

**Target**: Q3 2024

### GraphQL Support

Alternative to REST API:

- GraphQL schema definition
- Query and mutation resolvers
- Integration with existing services
- GraphQL playground
- DataLoader for N+1 query optimization

### Audit Logging

Track all system changes:

- Audit log model and tables
- Automatic logging of CRUD operations
- User action tracking
- Queryable audit history
- Compliance reporting

### File Upload/Storage

Handle file operations:

- Local file storage
- Cloud storage integration (S3, Azure Blob, GCS)
- File validation (size, type)
- Image processing (resize, thumbnails)
- Secure file serving

### Background Tasks

Asynchronous job processing:

- Celery integration
- Redis or RabbitMQ as message broker
- Task scheduling (cron-like)
- Task monitoring dashboard
- Email queuing
- Report generation

## Long Term (v2.0.0)

**Target**: Q4 2024

### Microservices Architecture

Break monolith into services:

- Service separation strategy
- Inter-service communication (gRPC, REST)
- API Gateway
- Service discovery
- Distributed tracing

### Multi-Tenancy

Support multiple organizations:

- Tenant isolation at database level
- Subdomain-based tenant resolution
- Tenant-specific configurations
- Shared schema vs. separate schema approaches
- Tenant onboarding workflow

### Advanced Search

Full-text search capabilities:

- Elasticsearch integration
- Search indexing pipeline
- Fuzzy search
- Faceted search
- Search analytics

### Monitoring & Observability

Production monitoring:

- Prometheus metrics
- Grafana dashboards
- Application performance monitoring (APM)
- Distributed tracing (Jaeger, Zipkin)
- Error tracking (Sentry)
- Health check endpoints

## Community Requests

Features requested by community (prioritized):

### High Priority

- [ ] OAuth2 social login (Google, GitHub, Facebook)
- [ ] Multi-language support (i18n)
- [ ] Export data (CSV, Excel, PDF)
- [ ] Email templates with HTML
- [ ] Password policies configuration
- [ ] Account lockout after failed attempts

### Medium Priority

- [ ] Caching layer (Redis)
- [ ] Admin dashboard UI
- [ ] API key authentication
- [ ] Webhook system
- [ ] Notification system (push, SMS)
- [ ] Data import/export tools

### Low Priority

- [ ] Mobile app (React Native)
- [ ] Desktop app (Electron)
- [ ] Browser extension
- [ ] CLI tool for API interaction
- [ ] API client SDKs (Python, JavaScript, Go)

## Research & Exploration

Technologies under consideration:

- **gRPC**: High-performance RPC framework
- **NATS**: Message streaming
- **TimescaleDB**: Time-series data
- **Apache Kafka**: Event streaming
- **Kubernetes**: Container orchestration
- **Terraform**: Infrastructure as code

## Breaking Changes

### v2.0.0 (Planned)

- Minimum Python version: 3.12
- Database schema changes for multi-tenancy
- API endpoint restructuring
- Configuration format changes

Migration guide will be provided.

## Contributing to Roadmap

We welcome suggestions!

### How to Propose Features

1. **Check existing requests**: Search issues and discussions
2. **Open discussion**: Explain use case and benefits
3. **Gather feedback**: Community votes and comments
4. **Create proposal**: Detailed implementation plan
5. **Submit PR**: Implement if approved

### Priority Factors

We prioritize based on:

- **Community demand**: Number of requests
- **Alignment**: Fits project goals
- **Complexity**: Implementation effort
- **Maintainability**: Long-term support needs
- **Dependencies**: External library maturity

## Release Schedule

- **Minor versions** (x.Y.0): Every 3 months
- **Patch versions** (x.y.Z): As needed for bugs
- **Major versions** (X.0.0): Yearly with breaking changes

## Stay Updated

- **GitHub Releases**: Watch repository
- **Discussions**: Join conversations
- **Twitter**: Follow project updates (if available)
- **Newsletter**: Subscribe for major announcements (if available)

## Need a Feature Now?

If you can't wait for official implementation:

1. **Fork** the repository
2. **Implement** the feature
3. **Share** via pull request
4. **Discuss** integration options

Or consider **hiring** a contributor for custom development.

## Questions?

- Feature requests: [GitHub Discussions](https://github.com/panjidwisatrio/fastapi-clean-architecture/discussions)
- Timeline questions: Open discussion
- Custom features: Contact maintainers

---

**Note**: This roadmap is aspirational and may change based on community needs, available resources, and project direction. No timeline is guaranteed.

Thank you for being part of our journey! 🚀
