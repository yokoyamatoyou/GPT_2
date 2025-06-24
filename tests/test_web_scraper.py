from src.tools.web_scraper import scrape_website_content


def test_scrape_local_html(tmp_path, monkeypatch):
    html = "<html><body><main><p>Hello</p><p>World</p></main></body></html>"
    file = tmp_path / "index.html"
    file.write_text(html, encoding="utf-8")

    def mock_get(url, **kwargs):
        class Resp:
            status_code = 200

            def raise_for_status(self):
                pass

            @property
            def content(self):
                return html.encode("utf-8")

        return Resp()

    monkeypatch.setattr("requests.get", mock_get)
    text = scrape_website_content("http://example.com")
    assert text == "Hello World"
