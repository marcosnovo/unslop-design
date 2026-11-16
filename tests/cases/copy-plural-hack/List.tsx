export const Count = ({ n }) => <p>{n} item(s) selected</p>;
export const Files = ({ n }) => <p>{`${n} file(s) uploaded`}</p>;
export const Header = () => <th>Tag(s)</th>;
// misses: code, not copy
export const clean = (names) => names.map((s) => trim(s));
export const ok = (s) => (isValid(s) ? "Valid" : "Check the address");
