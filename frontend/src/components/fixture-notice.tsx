type FixtureNoticeProps = {
  children: string;
};

export function FixtureNotice({ children }: FixtureNoticeProps) {
  return (
    <aside className="fixture-notice" data-development-fixture="true">
      <span aria-hidden="true" />
      <p>{children}</p>
    </aside>
  );
}
