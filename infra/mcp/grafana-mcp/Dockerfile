FROM golang:1.26-alpine AS builder
RUN go install github.com/grafana/mcp-grafana/cmd/mcp-grafana@latest

FROM alpine:latest
COPY --from=builder /go/bin/mcp-grafana /usr/local/bin/mcp-grafana
ENTRYPOINT ["mcp-grafana"]
