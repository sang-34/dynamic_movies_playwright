from playwright.sync_api import Page, Response


def register_api_observer(page: Page) -> None:

    def handle_response(response: Response) -> None:
        try:
            if "/api/movie" not in response.url:
                return

            request = response.request

            print(
                f"[API] "
                f"status={response.status} "
                f"method={request.method} "
                f"resource_type={request.resource_type} "
                f"url={response.url}"
            )
        except Exception as exc:
            print(f"[API observer error] {exc}")

    page.on("response", handle_response)
