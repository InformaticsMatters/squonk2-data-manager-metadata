# The Metadata behaviour (
_METADATA_VERSION: str = '0.0.0'


def version() -> str:
    return _METADATA_VERSION


if __name__ == "__main__":
    print('Data Manager Metadata (v%s)', _METADATA_VERSION)
