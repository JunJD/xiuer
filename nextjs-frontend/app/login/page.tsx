
import LoginForm from './login-form';

type Props = {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export default async function Page({ searchParams }: Props) {
  const params = await searchParams;
  const redirectUrl = params.redirect as string | undefined;
  return <LoginForm redirectUrl={redirectUrl} />;
}
