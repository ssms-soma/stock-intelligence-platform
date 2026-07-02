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
  return (
    <div className="company-profile-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CompanyProfileCard({ profile, loading, error }) {
  if (loading) {
    return (
      <section className="company-profile-card">
        <p className="company-profile-eyebrow">Company Intelligence</p>
        <p className="company-profile-muted">Loading company profile...</p>
      </section>
    );
  }

  if (error && !profile) {
    return (
      <section className="company-profile-card">
        <p className="company-profile-eyebrow">Company Intelligence</p>
        <p className="company-profile-muted">{error}</p>
      </section>
    );
  }

  if (!profile) {
    return null;
  }

  const companyName =
    renderValue(profile.long_name, null) ||
    renderValue(profile.short_name, null) ||
    renderValue(profile.name, profile.ticker);
  const location = [profile.city, profile.state, profile.country]
    .filter(Boolean)
    .join(", ");
  const summary = renderValue(
    profile.short_summary || profile.business_summary || profile.description,
    "Business summary is not available yet."
  );
  const currencyValue = profile.currency_symbol
    ? `${profile.currency_symbol} ${renderValue(profile.currency)}`
    : renderValue(profile.currency);

  return (
    <section className="company-profile-card">
      <div className="company-profile-header">
        <div>
          <p className="company-profile-eyebrow">Company Intelligence</p>
          <h2>{companyName}</h2>
          <p className="company-profile-muted">
            {renderValue(profile.ticker)}
            {" | "}
            {renderValue(profile.quote_type, "Equity")}
          </p>
        </div>
        {profile.logo_url && (
          <img
            className="company-profile-logo"
            src={profile.logo_url}
            alt={`${companyName} logo`}
          />
        )}
      </div>

      <div className="company-profile-grid">
        <ProfileItem label="Sector" value={renderValue(profile.sector)} />
        <ProfileItem label="Industry" value={renderValue(profile.industry)} />
        <ProfileItem label="Country" value={renderValue(profile.country)} />
        <ProfileItem label="Exchange" value={renderValue(profile.exchange)} />
        <ProfileItem label="Currency" value={currencyValue} />
        <ProfileItem label="Market" value={renderValue(profile.market)} />
        <ProfileItem
          label="Employees"
          value={formatEmployees(profile.employees)}
        />
        <ProfileItem label="Location" value={renderValue(location)} />
      </div>

      {profile.website && (
        <a
          className="company-profile-link"
          href={profile.website}
          target="_blank"
          rel="noreferrer"
        >
          {profile.website}
        </a>
      )}

      <p className="company-profile-summary">{summary}</p>
    </section>
  );
}

export default CompanyProfileCard;
