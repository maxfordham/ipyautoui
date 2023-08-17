# +
# auiwidgets.AutoMarkdown(CoreIpywidgets.model_json_schema()["properties"]["markdown"])
# -

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    di = CoreIpywidgets.model_json_schema()["properties"]["markdown"]
    di_ = CoreIpywidgets.model_json_schema()["properties"]["text_area"]
    print("test markdown - ")
    print(is_Markdown(di))
    print(is_Text(di))
    print(is_Textarea(di))
    print("----------------")
    print("test Textarea - ")
    print(is_Markdown(di_))
    print(is_Text(di_))
    print(is_Textarea(di_))
