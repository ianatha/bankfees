"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PdfViewer } from "@/components/pdf-viewer";
import { Worker } from "@react-pdf-viewer/core";
import { Viewer } from "@react-pdf-viewer/core";
import "@react-pdf-viewer/core/lib/styles/index.css";
import { bookmarkPlugin } from "@react-pdf-viewer/bookmark";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import { highlightPlugin, RenderHighlightsProps, Trigger } from "@react-pdf-viewer/highlight";
import { Plugin, PluginOnTextLayerRender } from "@react-pdf-viewer/core";

const findLinksPlugin = (): Plugin => {
  const findLinks = (e: PluginOnTextLayerRender) => {
    console.log("1", e);

    e.ele.querySelectorAll(".rpv-core__text-layer-text").forEach((textEle) => {
      const el = textEle as HTMLElement;
      el.style.setProperty("background-color", "red", "important");
    });
    // e.ele.style.setProperty("background-color", "red", "important");
    // `rpv-core-text` is the CSS class of each text element
    // .querySelectorAll(".rpv-core-text")
    // .forEach((textEle) => {
    //   console.log("@", el);
    //   debugger;
    //   // linkifyElement(textEle as HTMLElement, {
    //   //     attributes: {
    //   //         // Custom styles
    //   //         style: 'color: transparent; text-decoration: none;',
    //   //         // Open link in new tab
    //   //         target: '_blank',
    //   //     },
    //   // });
    // });
  };

  return {
    onTextLayerRender: findLinks,
  };
};

export function PdfDebug() {
  const [testUrl, setTestUrl] = useState(
    "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf"
  );
  const [currentUrl, setCurrentUrl] = useState("");

  const loadTestPdf = () => {
    setCurrentUrl(testUrl);
  };
  const areas = [
    {
      pageIndex: 3,
      height: 1.55401,
      width: 28.1674,
      left: 27.5399,
      top: 15.0772,
    },
    {
      pageIndex: 3,
      height: 1.32637,
      width: 37.477,
      left: 55.7062,
      top: 15.2715,
    },
    {
      pageIndex: 3,
      height: 1.55401,
      width: 28.7437,
      left: 16.3638,
      top: 16.6616,
    },
  ];

  const bookmarkPluginInstance = bookmarkPlugin();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const findLinksPluginInstance = findLinksPlugin();
  const renderHighlights = (props: RenderHighlightsProps) => (
    <div>
      {areas
        .filter((area) => area.pageIndex === props.pageIndex)
        .map((area, idx) => (
          <div
            key={idx}
            className="highlight-area"
            style={Object.assign(
              {},
              {
                background: "yellow",
                opacity: 0.4,
              },
              props.getCssProperties(area, props.rotation)
            )}
          />
        ))}
    </div>
  );

  const highlightPluginInstance = highlightPlugin({
    renderHighlights,

    trigger: Trigger.TextSelection,
  });

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-2">
        <Input
          value={testUrl}
          onChange={(e) => setTestUrl(e.target.value)}
          placeholder="Enter PDF URL to test"
          className="flex-1"
        />
        <Button onClick={loadTestPdf}>Load PDF</Button>
      </div>

      {currentUrl && (
        <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
          <div
            style={{
              border: "1px solid rgba(0, 0, 0, 0.3)",
              height: "750px",
            }}
          >
            <Viewer
              fileUrl={currentUrl}
              plugins={[
                defaultLayoutPluginInstance,
                bookmarkPluginInstance,
                highlightPluginInstance,
                findLinksPluginInstance,
              ]}
              initialPage={3}
            />
          </div>
        </Worker>

        // <div className="h-[600px] border rounded-lg overflow-hidden">
        //   <PdfViewer documentUrl={currentUrl} pageNumber={1} searchTerm="" highlight="" />
        // </div>
      )}
    </div>
  );
}

export default function DebugPage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-2xl font-bold mb-4">PDF Debug Page</h1>
        <p className="text-slate-600 mb-8">Use this page to test PDF loading functionality</p>
        <PdfDebug />
      </div>
    </main>
  );
}
