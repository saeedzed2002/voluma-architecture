type FixtureNoticeProps = {
  children: string;
};

export function FixtureNotice({ children }: FixtureNoticeProps) {
  if (process.env.NODE_ENV !== "development") return null;

  return (
    <aside className="fixture-notice" data-development-fixture="true">
      <span aria-hidden="true" />
      <p>{children}</p>
    </aside>
  );
}
