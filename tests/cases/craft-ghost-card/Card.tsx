export const Card = ({ children }) => <div className="rounded-xl border bg-card text-card-foreground shadow">{children}</div>;
export const Flat = ({ children }) => <div className="rounded-xl border bg-card">{children}</div>;
export const Lift = ({ children }) => <div className="rounded-xl bg-card shadow-md">{children}</div>;
export const Hover = ({ children }) => <div className="rounded-xl border hover:shadow-md">{children}</div>;
