function renderValue(value, fallback = "N/A") {
  if (value === null || value === undefined || value === "") return fallback;
  return value;
}

function formatEmployees(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value);
  }

  return numberValue.toLocaleString();
}

function ProfileItem({ label, value }) {
  if (value === null || value === undefined || value === "") return null;

  return (
    <div className="company-profile-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CompanyProfileCard({ profile, stockData, loading, error }) {
  if (loading) {
    return (
      <section className="company-profile-card">
        <p className="company-profile-eyebrow">Company Intelligence</p>
        <p className="company-profile-muted">Loading company profile...</p>
      </section>
    );
  }

  if (error && !profile && !stockData) {
    return (
      <section className="company-profile-card">
        <p className="company-profile-eyebrow">Company Intelligence</p>
        <p className="company-profile-muted">{error}</p>
      </section>
    );
  }

  if (!profile && !stockData) {
    return null;
  }

  const safeProfile = profile || {};

  const mergedProfile = {
    ...stockData,
    ...Object.fromEntries(
      Object.entries(safeProfile).filter(([, value]) => value != null && value !== "")
    ),
  };
  const companyName =
    renderValue(mergedProfile.long_name, null) ||
    renderValue(mergedProfile.short_name, null) ||
    renderValue(mergedProfile.name, null) ||
    renderValue(mergedProfile.company_name, mergedProfile.ticker);
  const location = [mergedProfile.city, mergedProfile.state, mergedProfile.country]
    .filter(Boolean)
    .join(", ");
  const summary =
    mergedProfile.short_summary ||
    mergedProfile.business_summary ||
    mergedProfile.description;
  const currencyValue = mergedProfile.currency_symbol
    ? `${mergedProfile.currency_symbol} ${mergedProfile.currency || ""}`.trim()
    : mergedProfile.currency;

  return (
    <section className="company-profile-card">
      <div className="company-profile-header">
        <div>
          <p className="company-profile-eyebrow">Company Intelligence</p>
          <h2>{companyName}</h2>
          <p className="company-profile-muted">
            {renderValue(mergedProfile.ticker)}
            {mergedProfile.quote_type && ` | ${mergedProfile.quote_type}`}
          </p>
        </div>
        {mergedProfile.logo_url && (
          <img
            className="company-profile-logo"
            src={mergedProfile.logo_url}
            alt={`${companyName} logo`}
          />
        )}
      </div>

      <div className="company-profile-grid">
        <ProfileItem label="Sector" value={mergedProfile.sector} />
        <ProfileItem label="Industry" value={mergedProfile.industry} />
        <ProfileItem label="Country" value={mergedProfile.country} />
        <ProfileItem label="Exchange" value={mergedProfile.exchange} />
        <ProfileItem label="Currency" value={currencyValue} />
        <ProfileItem label="Market" value={mergedProfile.market} />
        <ProfileItem
          label="Employees"
          value={mergedProfile.employees ? formatEmployees(mergedProfile.employees) : null}
        />
        <ProfileItem label="Location" value={location || null} />
      </div>

      {mergedProfile.website && (
        <a
          className="company-profile-link"
          href={mergedProfile.website}
          target="_blank"
          rel="noreferrer"
        >
          {mergedProfile.website}
        </a>
      )}

      <p className="company-profile-summary">
        {summary || "Extended company profile information is temporarily unavailable."}
      </p>
    </section>
  );
}

export default CompanyProfileCard;
