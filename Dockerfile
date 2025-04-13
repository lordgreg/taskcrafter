FROM busybox

RUN mkdir -p /app/taskcrafter
WORKDIR /app/taskcrafter

COPY dist/taskcrafter /app/taskcrafter
COPY jobs /app/taskcrafter/jobs

RUN adduser -D taskcrafter
RUN chown -R taskcrafter:taskcrafter /app/taskcrafter
USER taskcrafter

ENTRYPOINT ["/app/taskcrafter/taskcrafter"]
