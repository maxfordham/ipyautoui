# +
# auiwidgets.AutoMarkdown(TestAutoLogic.schema()["properties"]["markdown"])
# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    di = TestAutoLogic.schema()["properties"]["markdown"]
    di_ = TestAutoLogic.schema()["properties"]["text_area"]
    print("test markdown - ")
    print(is_Markdown(di))
    print(is_Text(di))
    print(is_Textarea(di))
    print("----------------")
    print("test Textarea - ")
    print(is_Markdown(di_))
    print(is_Text(di_))
    print(is_Textarea(di_))


if __name__ == "__main__":
    m = automapschema(
        {
            "title": "Int Slider",
            "default": 2,
            "minimum": 0,
            "maximum": 3,
            "type": "integer",
        }
    )

    display(m)

if __name__ == "__main__":
    ui = widgetcaller(m)
    display(ui)

if __name__ == "__main__":
    m = automapschema(
        {
            "title": "Array",
            "default": ["f", "d"],
            "maxItems": 5,
            "type": "array",
            "items": {"type": "string"},
        }
    )

    display(m)

if __name__ == "__main__":
    ui = widgetcaller(m)
    display(ui)

if __name__ == "__main__":
    w = autowidget(
        {
            "title": "Int Slider",
            "default": 2,
            "minimum": 0,
            "maximum": 3,
            "type": "integer",
        }
    )

    display(w)

if __name__ == "__main__":
    s = TestAutoLogic.schema()
    # display(s)
    m = automapschema(s)
    display(m)

if __name__ == "__main__":
    display(widgets.VBox([widgetcaller(v) for k, v in m.items()]))
