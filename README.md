# Vanity git.io
## Or: Why URL shorteners need (some) quotas.

git.io is a really useful shortener for your GitHub-related URLs and it even [supports the creation of custom URLs](https://github.blog/2011-11-10-git-io-github-url-shortener/).

Not having the need to authorize prior to the creation of custom URLs is very practical, but is also enables the mass-creation of an endless list of customized URLs at once [**without giving other persons the chance to benefit from them**](#why-has-this-been-published).

This small Proof-of-Concept fulfills two purposes:
1. Highlight the risks of enabling the handy custom URL shortener feature without authorisation (also good to know if you design your own shortener)
2. Provide a demo in form of a simple Python CLI for git.io to create your own custom URL(s) as long as they are free

> You might notice that the two forces are reciprocal. This is by intention: First, educating what the problem is hopefully helps with building an intuition of fair usage. Second, finding a custom URL that is still free in the wild becomes more and more harder, thus a tool that automatizes the process is a nice-to-have (at least), while still staying fair.


## The 'Algorithm'

In general, the algorithm to mass-create short URLs is quite simple - which is basically what the provided CLI does (simplified): 

```python
for code in short_code:
   target_url = url(f"{target_url}?{code}")
   short_url = url(code) 
   if not redirect(from=short_url, to=target_url):
      shortener.register(code, target_url)
      # Verify that redirection works using the shortened code url:
      if redirect(from=short_url, to=target_url).ok:
         print("Success")
      else:
         print("Something went wrong")
```

To use **one and the same target** a cheap trick comes in handy: Transform the target URL a bit by appending "useless" information. 

For example, we can append a `?{code}` (see line 2) or `#{code}` to our target: `http://github.com/kdevo/vanity-git.io` is transformed to `http://github.com/kdevo/vanity-git.io?kdevo` with `https://git.io/kdevo` as a short URL.
This way, the main segment path of the URL will not get modified and the shortened URL still essentially points to the same site - as long as the query parameter is unknown to the target, this will not trigger any unwanted behavior.

## Why has this been published?

I saw that a small group of GitHub users already mass-created many 1-(unicode)char git.io URLs to one and the same site by using the trick above. I decided to re-balance it by giving more people the chance (using the CLI) to at least do mass-tests (and a hard-coded quota of the creation of 5 custom URLs in one batch). This comes with a disclaimer:

> :warning: **Stay fair** and don't use this for spamming. Only create URLs you really need and which have a purpose.

## The Countermeasures

More democratic but also more impractical would be the use of quotas (say 10 custom URLs per day).
This requires either 
1. the tracking of PII (personally identifiable information) such as IP address or...
2. a kind of authentication (is the user registered and logged in?) followed by authorisation (is the user allowed to *create* another custom URL at this moment?)

It makes everything slightly more complicated, but the resulting fairness would be totally worth it.

## Usage 

Simple:
Ensure `requests` is installed and get help by executing `./vanity-gitio.py --help` for usage info. 
