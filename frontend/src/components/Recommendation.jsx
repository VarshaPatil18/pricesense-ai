export default function Recommendation({ data }) {
  return (
    <div className="recommendation">
      <h3>AI Recommendation</h3>
      <p>
        <strong>Best Platform:</strong> {data.recommended}
      </p>
      <p>{data.explanation}</p>
      <small>
        Powered by Microsoft Azure OpenAI & Azure Machine Learning
      </small>
    </div>
  );
}
