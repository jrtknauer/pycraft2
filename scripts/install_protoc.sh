#!/bin/bash -eux
#
# Download and install the SC2API compatible protoc binary

PROTOC_VERSION="protoc-23.2-linux-x86_32"
PROTOC="protoc"
PROTOC_DIR="/usr/bin"
PROTOC_BINARY="${PROTOC_DIR}/$PROTOC"

# Do not arbitrarily delete other protoc binaries - they may not be the same version.
if [ -e "$PROTOC_BINARY" ]; then
    echo "$PROTOC_BINARY already exists."
    exit 1
fi

# Download, install, change permissions, and cleanup.
wget -q "https://github.com/protocolbuffers/protobuf/releases/download/v23.2/protoc-23.2-linux-x86_32.zip"
unzip -q "${PROTOC_VERSION}.zip" -d "$PROTOC_VERSION"
cp "${PROTOC_VERSION}/bin/${PROTOC}" "$PROTOC_BINARY"
chmod +x "$PROTOC_BINARY"
rm -rf "${PROTOC_VERSION}.zip" "$PROTOC_VERSION"
