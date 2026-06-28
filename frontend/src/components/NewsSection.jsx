import NewsCard from "./NewsCard";

function NewsSection({ newsData }) {
  return (
    <div style={{ marginTop: "3rem" }}>
      <h2>Latest News</h2>

      {newsData.map((article) => (
        <NewsCard article={article} key={article.url} />
      ))}
    </div>
  );
}

export default NewsSection;
