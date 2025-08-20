import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';

function App() {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<any>(null);

  const samplePrompts = [
    "Write a romantic comedy about two rival chefs.",
    "Create a thriller about a missing artifact.",
    "Generate a sci-fi story set on Mars.",
    "Write a drama about family secrets.",
    "Create a horror story in an abandoned hospital."
  ];

  const handleSampleClick = (prompt: string) => {
    setUserInput(prompt);
  };

  const handleGenerate = async () => {
    if (!userInput.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/generate-story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedContent(data);
    } catch (error) {
      console.error('Error generating screenplay:', error);
      setGeneratedContent({
        error: 'Failed to generate screenplay. Make sure the backend server is running on port 8000.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const formatGeneratedContent = () => {
    if (!generatedContent) {
      return "Your screenplay will appear here...";
    }

    if (generatedContent.error) {
      return (
        <div className="text-red-400">
          {generatedContent.error}
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {generatedContent.genre && generatedContent.tone && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Genre & Tone</h3>
            <p className="text-gray-300">
              <span className="font-medium">Genre:</span> {generatedContent.genre}
            </p>
            <p className="text-gray-300">
              <span className="font-medium">Tone:</span> {generatedContent.tone}
            </p>
          </div>
        )}

        {generatedContent.outline && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Plot Outline</h3>
            <p className="text-gray-300 leading-relaxed">{generatedContent.outline}</p>
          </div>
        )}

        {generatedContent.scene && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Key Scene</h3>
            <p className="text-gray-300 leading-relaxed">{generatedContent.scene}</p>
          </div>
        )}

        {generatedContent.dialogue && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">Dialogue</h3>
            <div className="text-gray-300 leading-relaxed whitespace-pre-line font-mono text-sm">
              {generatedContent.dialogue}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Left Column - Input Section */}
          <div className="bg-slate-800 rounded-lg p-6">
            <h1 className="text-2xl font-bold text-white mb-6">Screenplay Generator</h1>
            
            {/* Sample Prompts */}
            <div className="space-y-3 mb-6">
              {samplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleClick(prompt)}
                  className="w-full text-left p-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-gray-300 hover:text-white transition-colors duration-200 text-sm"
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Text Input */}
            <div className="mb-6">
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Enter your prompt here..."
                className="w-full h-32 p-4 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-blue-500 focus:outline-none resize-none placeholder-gray-400"
              />
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!userInput.trim() || isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin w-5 h-5 mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Screenplay'
              )}
            </button>
          </div>

          {/* Right Column - Output Section */}
          <div className="bg-slate-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Generated Screenplay</h2>
            
            <div className="bg-slate-700 rounded-lg p-6 h-full min-h-96 overflow-y-auto">
              <div className="text-gray-400 font-mono text-sm">
                {formatGeneratedContent()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;