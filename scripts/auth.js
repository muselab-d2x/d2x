const { execSync } = require('child_process');
const { writeFileSync, unlinkSync, existsSync, mkdirSync } = require('fs');

const checkEnvVars = (prefixes) => {
    const missingVars = [];
    prefixes.forEach(prefix => {
        if (!process.env[`${prefix}_AUTH_URL`] && 
            (!process.env[`${prefix}_ACCESS_TOKEN`] || !process.env[`${prefix}_INSTANCE_URL`]) && 
            (!process.env[`${prefix}_USERNAME`] || !process.env[`${prefix}_CLIENT_ID`] || !process.env[`${prefix}_PRIVATE_KEY`])) {
            missingVars.push(prefix);
        }
    });
    return missingVars;
};

const authenticateOrgJwt = (username, clientId, privateKey, alias) => {
    console.log(`Authenticating to ${alias} using JWT...`);
    const keyFilePath = `/tmp/${alias}_key`;
    writeFileSync(keyFilePath, privateKey);

    try {
        execSync(`sf org login jwt --username ${username} --jwt-key-file ${keyFilePath} --client-id ${clientId} --alias ${alias} --set-default-dev-hub`);
        console.log(`Successfully authenticated ${alias} using JWT.`);
    } catch (error) {
        console.error(`Failed to authenticate ${alias} using JWT.`);
        process.exit(1);
    } finally {
        unlinkSync(keyFilePath);
    }
};

const authenticateOrgAuthUrl = (authUrl, alias) => {
    console.log(`Authenticating to ${alias} using auth url...`);
    const authUrlFilePath = `/tmp/${alias}_auth_url`;
    writeFileSync(authUrlFilePath, authUrl);

    try {
        execSync(`sfdx org login sfdx-url -f ${authUrlFilePath} -a ${alias} -d`);
        console.log(`Successfully authenticated ${alias} using auth url.`);
    } catch (error) {
        console.error(`Failed to authenticate ${alias} using auth url.`);
        process.exit(1);
    } finally {
        unlinkSync(authUrlFilePath);
    }
};

const authenticateOrgAccessToken = (accessToken, instanceUrl, alias) => {
    console.log(`Authenticating to ${alias} using access token...`);

    try {
        execSync(`sf org login access-token --instance-url ${instanceUrl} --access-token ${accessToken} --alias ${alias} --no-prompt`);
        console.log(`Successfully authenticated ${alias} using access token.`);
    } catch (error) {
        console.error(`Failed to authenticate ${alias} using access token.`);
        process.exit(1);
    }
};

const authenticateOrg = (prefix, alias, check_only = false) => {
    if (process.env[`${prefix}_AUTH_URL`]) {
        if (check_only) {
            return true;
        }
        authenticateOrgAuthUrl(process.env[`${prefix}_AUTH_URL`], alias);
    } else if (process.env[`${prefix}_ACCESS_TOKEN`] && process.env[`${prefix}_INSTANCE_URL`]) {
        if (check_only) {
            return true;
        }
        authenticateOrgAccessToken(process.env[`${prefix}_ACCESS_TOKEN`], process.env[`${prefix}_INSTANCE_URL`], alias);
    } else if (process.env[`${prefix}_USERNAME`] && process.env[`${prefix}_CLIENT_ID`] && process.env[`${prefix}_PRIVATE_KEY`]) {
        if (check_only) {
            return true;
        }
        authenticateOrgJwt(process.env[`${prefix}_USERNAME`], process.env[`${prefix}_CLIENT_ID`], process.env[`${prefix}_PRIVATE_KEY`], alias);
    } else {
        console.error(`No valid authentication method found for ${alias}. Skipping.`);
        process.exit(1);
    }

    // Verify authentication
    try {
        execSync(`sfdx force:org:display -u ${alias}`);
    } catch {
        console.error(`Failed to authenticate ${alias}.`);
        process.exit(1);
    }

    // Import the org to CumulusCI
    execSync(`cci org import ${alias} ${alias}`);
};

const main = () => {
    if (existsSync('~/.orgs_authenticated')) {
        return;
    }

    const environment = process.env.USER === 'd2x' ? 'Codespaces' : 'GitHub Actions';

    const args = process.argv.slice(2);
    const orgMapping = {};
    const missingVars = [];

    if (args.length === 0) {
        const defaultPrefixes = ['DEV_HUB', 'PACKAGING_ORG', 'TARGET_ORG'];
        missingVars.push(...checkEnvVars(defaultPrefixes));
    } else {
        args.forEach(arg => {
            const prefixes = arg.split('|');
            missingVars.push(...checkEnvVars(prefixes));
        });
    }

    if (missingVars.length > 0) {
        console.error(`Missing required environment variables for the following prefixes: ${missingVars.join(', ')}`);
        process.exit(1);
    }

    if (args.length === 0) {
        available = {
            DEV_HUB: null,
            PACKAGING_ORG: null,
            TARGET_ORG: null
        }
        available.DEV_HUB = authenticateOrg('DEV_HUB', 'devhub', check_only = true);
        try {
            available.PACKAGING_ORG = authenticateOrg('PACKAGING_ORG', 'packaging', check_only = true);
        } catch (error) {
            console.info('No packaging org found. Skipping.');
        }
        try {
            available.TARGET_ORG = authenticateOrg('TARGET_ORG', 'target', check_only = true);
        } catch (error) {
            console.info('No packaging org found. Skipping.');
        }
        if (! available.DEV_HUB) {
            console.error('No dev hub found. Pass the DEV_HUB_AUTH_URL or the environment variables for jwt auth. Exiting.');
            process.exit(1);
        }
    } else {
        args.forEach(arg => {
            const prefixes = arg.split('|');
            const primaryPrefix = prefixes[0];
            const alias = primaryPrefix.toLowerCase();

            for (const prefix of prefixes) {
                try {
                    authenticateOrg(prefix, alias);
                    orgMapping[alias] = prefix;
                    break;
                } catch (error) {
                    console.error(error.message);
                }
            }
        });
    }

    // Write the org mapping to a file
    writeFileSync('org_mapping.txt', 'Org to Prefix Mapping:\n' + Object.entries(orgMapping).map(([alias, prefix]) => `${alias}: ${prefix}`).join('\n'));

    // Set default org if running as user 'd2x'
    if (process.env.USER === 'd2x') {
        console.log('Setting dev as the default org');
        execSync('cci org default dev');
    }

    // Ensure the force-app/main/default folder exists
    if (!existsSync('force-app/main/default')) {
        mkdirSync('force-app/main/default', { recursive: true });
    }

    // Mark the script as having authenticated
    writeFileSync('~/.orgs_authenticated', '');

    // Provide error message if any required org is not authenticated
    if (Object.keys(orgMapping).length === 0) {
        console.error('Error: One or more required orgs were not authenticated.');
        if (environment === 'Codespaces') {
            console.error('Please set the appropriate secrets in your Codespaces environment.');
        } else {
            console.error('Please set the appropriate secrets in your GitHub Actions environment.');
        }
        process.exit(1);
    }
};

main();