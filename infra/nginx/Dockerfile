FROM nginx:1.30.4-alpine-slim@sha256:77da26c31397bf6694b4bf93275f5b40b0b120ba1b8f114264b603e592c561d6

COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
COPY infra/nginx/conf.d/media.conf /etc/nginx/conf.d/media.conf
COPY infra/nginx/conf.d/proxy-headers.conf /etc/nginx/conf.d/proxy-headers.conf
COPY --chmod=755 infra/nginx/entrypoint.sh /usr/local/bin/voluma-nginx-entrypoint

EXPOSE 8080 8443

ENTRYPOINT ["/usr/local/bin/voluma-nginx-entrypoint"]
CMD ["nginx", "-g", "daemon off;"]
