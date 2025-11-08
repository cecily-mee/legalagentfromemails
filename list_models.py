from google.ai import generativelanguage_v1beta as gl
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import os
import sys


def main():
    # Try to create the client using Application Default Credentials (ADC).
    try:
        client = gl.ModelServiceClient()
    except DefaultCredentialsError:
        # Fall back to a service account JSON file if provided by env vars.
        sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("SERVICE_ACCOUNT_FILE")
        if sa_path and os.path.exists(sa_path):
            creds = service_account.Credentials.from_service_account_file(sa_path)
            client = gl.ModelServiceClient(credentials=creds)
        else:
            print("Default credentials were not found.")
            print()
            print("Options to fix:")
            print("  1) Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path to a service account JSON file:")
            print(r"     set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json")
            print("  2) Or run: gcloud auth application-default login (uses your user credentials)")
            print("  3) Or set SERVICE_ACCOUNT_FILE to the path of a service account JSON and re-run this script.")
            print()
            print("See: https://cloud.google.com/docs/authentication/external/set-up-adc")
            sys.exit(1)

    # List models and print basic metadata.
    page = client.list_models()
    for m in page:
        methods = getattr(m, "supported_methods", None)
        print(m.name, "—", methods if methods is not None else "(no supported_methods field)")


if __name__ == "__main__":
    main()
