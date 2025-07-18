
import LoginForm from './login-form';

export default function Page({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const redirectUrl = searchParams.redirect as string | undefined;
  return <LoginForm redirectUrl={redirectUrl} />;
}
