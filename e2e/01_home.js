import { Selector } from 'testcafe'

fixture`Homepage exists`
  .page`http://localhost:8000`

test('Access the homepage', async t => {
  await t
    .expect(Selector('a').withAttribute('href', '/login/').innerText).contains('Log In')
})
