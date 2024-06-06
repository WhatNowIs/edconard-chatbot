// usePDFViewer.ts
import { useState, useCallback } from "react";

export const zoomLevels = [
  "50%",
  "80%",
  "100%",
  "130%",
  "200%",
  "300%",
  "400%",
];

const usePDFViewer = () => {
  const [scrolledIndex, setScrolledIndex] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [scaleFit, setScaleFit] = useState(1.0);

  const setCurrentPageNumber = useCallback((n: number) => {
    setScrolledIndex(n);
  }, []);


  return {
    scrolledIndex,
    setCurrentPageNumber,
    scale,
    setScaleFit,
  };
};

export default usePDFViewer;
