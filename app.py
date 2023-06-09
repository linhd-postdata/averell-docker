import copy
import json

from pathlib import Path
from zipfile import ZipFile

import gradio as gr
import pycountry

from averell.utils import get_ids, generate_tei, CORPORA_SOURCES
from averell.core import export_corpora

PARAMS = {
    "granularity": "poem",
    "output_format": "JSON",
    "corpora_list": [
        'bibit', 'stichopt', 'disco2_1',
        'disco3', 'adso', 'adso100',
        'plc', 'gongo', 'ecpa',
        '4b4v', 'czverse', 'mel'
    ],
}

def get_available_languages(sources):
    available_langs = []
    for c in sources:
        lg = c["properties"]["language"]
        if lg not in available_langs:
            available_langs.append(lg)
    return available_langs

def filter_corpus_language(sources, lg):
    corpora_sources = copy.deepcopy(sources)
    filtered_corpora = [c for c in corpora_sources if c["properties"]["language"] == lg]
    return filtered_corpora

available_languages = get_available_languages(CORPORA_SOURCES)

with gr.Blocks() as app_averell:
    def export(output_path, output_format, output_granularity):
        corpora_list = PARAMS["corpora_list"]
        if not corpora_list:
            return {out_file: gr.File.update(label="ERROR: No corpus selected")}
        output_path = output_path["label"]
        filename = f"corpora/{output_format}.zip"
        # Export to TEI
        if output_format == "TEI":
            generate_tei(corpora_list, output_path, True)
            return {out_file: gr.File.update(value=f"corpus/{output_format}.zip",
                                             label=output_format)}
        # Export to JSON
        if output_granularity == "poem":
            export_corpora(get_ids(corpora_list),
                           None,
                           "corpora/JSON",
                           None,
                           no_download=False,
                           ui_mode=True)
            with ZipFile(filename, "w") as zfile:
                for corp in corpora_list:
                    p = Path(f'{output_path}/{output_format}/{corp}')
                    for f in p.glob("**/*.json"):
                        zfile.write(f)
            return {out_file: gr.File.update(value=f"corpora/{output_format}.zip",
                                             label=output_format)}
        else:
            json_l, filename = export_corpora(get_ids(corpora_list),
                                                 output_granularity,
                                                 "corpus/JSON",
                                                 None,
                                                 no_download=False,
                                                 ui_mode=True)
            with open(f"corpora/{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(json_l, f, ensure_ascii=False, indent=4)
            return {out_file: gr.File.update(value=f"corpora/{filename}.json",
                                             label=filename)}


    def block_granularity(r_format):
        if r_format == "TEI":
            PARAMS["output_format"] = r_format
            return {rad_granularity: gr.update(value="poem", visible=False)}
        else:
            PARAMS["output_format"] = r_format
            return {rad_granularity: gr.update(value="poem", visible=True)}
    def update_granularity(value):
        PARAMS["granularity"] = value
        true_l = [gr.Checkbox.update(value=True, visible=True)]
        false_l = [gr.Checkbox.update(value=False, visible=False)] # False
        true_acc = [gr.Box.update(visible=True)]
        false_acc = [gr.Box.update(visible=False)] # False
        if value == "word":
            # 000011100110 + 110110 + 110110
            corp_list = false_l*4 + true_l*3 + false_l*2 + true_l*2 + false_l
            lang_list = true_l*2 + false_l + true_l*2 + false_l
            acc_list = true_acc*2 + false_acc + true_acc*2 + false_acc
            PARAMS["corpora_list"] = ["plc", "gongo", "ecpa", "bibit", "czverse"]
            return corp_list + lang_list + acc_list
        elif value == "syllable":
            # 000011000000 + 100000 + 100000
            corp_list = false_l*4 + true_l*2 + false_l*6
            lang_list = true_l + false_l*5
            acc_list = true_acc + false_acc*5
            PARAMS["corpora_list"] = ["plc", "gongo"]
            return corp_list + lang_list + acc_list
        else:
            return true_l*18 + true_acc*6


    def change_selection(value, *labels):
        for corpus_name in labels:
            update_corpora_list(value, corpus_name)
        return value
    def change_global_selection(value, *labels):
        for corpus_name in labels:
            update_corpora_list(value, corpus_name)
        return [gr.Checkbox.update(value=value)] * 6
    def update_corpora_list(added, corpus_name):
        corpora_list = PARAMS["corpora_list"]
        if corpus_name in corpora_list and not added:
            corpora_list.remove(corpus_name)
        elif corpus_name not in corpora_list and added:
            corpora_list.append(corpus_name)

    app_title = gr.HTML("<h1>Averell</h1>")
    with gr.Row() as row:
        with gr.Column(scale=3) as c1:
            rad_format = gr.Radio(["TEI", "JSON"],
                                  label="Output",
                                  info="Choose output format",
                                  value="TEI",
                                  interactive=True)
            rad_granularity = gr.Radio(
                ["poem", "stanza", "line", "word", "syllable"],
                label="Granularity",
                info="Choose output granularity",
                value="poem",
                interactive=True,
                visible=False,
                )
            corpus_checkboxes = []
            lang_checkboxes = []
            with gr.Box() as b1:
                gr.HTML(value="<h3>Corpora list<h3>")
                gr.HTML(value="<br>")
                all_corp_chk = gr.Checkbox(True, label="Select all/none",
                                           interactive=True)
                with gr.Row() as rowa:
                    all_label_list = []
                    gr.Checkbox(label="dummy",visible=False)
                    for lang in available_languages:
                        with gr.Column() as b2:
                            language = pycountry.languages.get(
                                alpha_2=lang).name
                            gr.HTML(language)
                            with gr.Blocks() as corpora:
                                with gr.Row() as rowb:
                                    lang_chk = gr.Checkbox(True,
                                                           label="Select all/none",
                                                           interactive=True)
                                    filtered_corpus = filter_corpus_language(
                                        CORPORA_SOURCES, lang)
                                    with gr.Accordion("Expand list",
                                                      open=False) as acc:
                                        label_list = []
                                        for corpus in filtered_corpus:
                                            classes = corpus["properties"][
                                                "granularity"]
                                            classes.append("poem")
                                            classes.append(lang)
                                            chk = gr.Checkbox(True,
                                                              label=corpus[
                                                                  "name"],
                                                              info=f'License: {corpus["properties"]["license"]} | Number of poems: {corpus["properties"]["doc_quantity"]}',
                                                              interactive=True,
                                                              elem_classes=classes,
                                                              elem_id=corpus[
                                                                  "properties"][
                                                                  "slug"],
                                                              )
                                            label = gr.Textbox(
                                                value=corpus["properties"][
                                                    "slug"], visible=False)
                                            # Corpus checkboxes change
                                            chk.change(update_corpora_list,
                                                       [chk, label],
                                                       show_progress=False)
                                            # "Select all" language checkboxes change
                                            lang_chk.change(change_selection,
                                                            [lang_chk,
                                                             *label_list],
                                                            chk,
                                                            show_progress=False)
                                            corpus_checkboxes.append(chk)
                                            label_list.append(label)
                                            all_label_list.append(label)
                                        lang_checkboxes.append(lang_chk)
                # "Select All/None" checkbox change
                all_corp_chk.change(change_global_selection,
                                    [all_corp_chk,
                                     *all_label_list],
                                    [*lang_checkboxes])
        with gr.Column(scale=1) as c2:
            accordions_boxes = rowa.children[1:]
            rad_granularity.change(update_granularity,
                                   rad_granularity,
                                   [*corpus_checkboxes,
                                    *lang_checkboxes,
                                    *accordions_boxes],
                                   show_progress=False)
            rad_format.change(block_granularity,
                              rad_format,
                              rad_granularity,
                              api_name="output_format",
                              show_progress=False)
            exp_btn = gr.Button("Export")
            folder_path = gr.Label(value="corpora/", visible=False)
            out_file = gr.File()
            exp_btn.click(export,
                          [folder_path,
                           rad_format,
                           rad_granularity],
                          out_file,
                          api_name="export")

app_averell.launch(share=False, server_name="0.0.0.0", server_port=5741)
