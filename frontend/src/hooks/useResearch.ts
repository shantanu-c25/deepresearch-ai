"use client";

import {
  useCallback,
  useState,
} from "react";

import {
  runResearch as requestResearch,
} from "@/lib/api";

import type {
  ResearchResponse,
} from "@/types/research";


export function useResearch() {
  const [
    question,
    setQuestionState,
  ] = useState("");

  const [
    result,
    setResult,
  ] = useState<ResearchResponse | null>(
    null
  );

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  const setQuestion = useCallback(
    (value: string) => {
      setQuestionState(value);

      if (error) {
        setError("");
      }
    },
    [error]
  );


  const submitResearch =
    useCallback(async () => {
      const trimmedQuestion =
        question.trim();

      if (!trimmedQuestion) {
        setError(
          "Please enter a research question."
        );

        setResult(null);

        return;
      }

      setIsLoading(true);
      setError("");
      setResult(null);

      try {
        const data =
          await requestResearch(
            trimmedQuestion
          );

        setResult(data);
      } catch (error) {
        if (
          error instanceof Error
        ) {
          setError(error.message);
        } else {
          setError(
            "Unable to complete the research. Please try again."
          );
        }
      } finally {
        setIsLoading(false);
      }
    }, [question]);


  const resetResearch =
    useCallback(() => {
      setQuestionState("");
      setResult(null);
      setError("");
      setIsLoading(false);
    }, []);


  return {
    question,
    setQuestion,
    result,
    isLoading,
    error,
    submitResearch,
    resetResearch,
  };
}