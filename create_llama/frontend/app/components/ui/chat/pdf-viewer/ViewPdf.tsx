
import { PDFOptionsBar } from "./PdfOptionsBar";
import React from "react";
import MemoizedVirtualizedPDF from "./VirtualizedPdf";
import { PdfDocument } from "@/app/types/document";
import  usePDFViewer  from "@/app/hooks/usePdfViewer";

interface ViewPdfProps {
  file: PdfDocument;
}

export const ViewPdf: React.FC<ViewPdfProps> = ({ file }) => {
  const {
    scrolledIndex,
    setCurrentPageNumber,
    scale,
    setScaleFit,
    numPages,
    setNumPages,
    handleZoomIn,
    handleZoomOut,
    nextPage,
    prevPage,
    scaleText,
    pdfFocusRef,
    goToPage,
    setZoomLevel,
    zoomInEnabled,
    zoomOutEnabled,
  } = usePDFViewer();

  return (
    <div className="flex flex-col">
      {scaleText && (
        <PDFOptionsBar
          scrolledIndex={scrolledIndex}
          numPages={numPages}
          scaleText={scaleText}
          nextPage={nextPage}
          prevPage={prevPage}
          handleZoomIn={handleZoomIn}
          handleZoomOut={handleZoomOut}
          goToPage={goToPage}
          setZoomLevel={setZoomLevel}
          zoomInEnabled={zoomInEnabled}
          zoomOutEnabled={zoomOutEnabled}
        />
      )}

      <MemoizedVirtualizedPDF
        key={`${file.id}`}
        ref={pdfFocusRef}
        file={file}
        setIndex={setCurrentPageNumber}
        scale={scale}
        setScaleFit={setScaleFit}
        setNumPages={setNumPages}
      />
    </div>
  );
};
