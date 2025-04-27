import dotenv from 'dotenv';

export class ConfigHelper {
    DB_PATH: string;

    constructor(envPath: string = './.env') {
        dotenv.config({ path: envPath });

        this.DB_PATH = process.env.DB_PATH ? process.env.DB_PATH : (() => { throw new Error("DB_PATH is not defined in the environment variables."); })();

        console.log("ConfigHelper initialized.");
    }

}