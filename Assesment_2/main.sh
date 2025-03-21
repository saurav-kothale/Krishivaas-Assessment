#!/bin/bash
cat <<EOF > Dockerfile
FROM python:3
RUN pip install numpy scipy pandas
CMD ["python", "./main.py"]
EOF

# sha1sum Dockerfile