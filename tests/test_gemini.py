from core.agent.GoogleLLM import Gemini


def test_gemini_integration():
    try:
        gemini = Gemini()
        gemini_response = gemini.simple_ask("Explain Fourier Transform in 2 sentences")

        print("--- Testing Simple Ask ---")
        print(gemini_response)

    except Exception as e:
        print(f"Error during Gemini test: {e}")


if __name__ == "__main__":
    test_gemini_integration()
