erDiagram
    JOB-TITLE }|--|| JOB-OFFER : has
    JOB-OFFER |o--|{ JOB-TO-SKILLS : maps
    JOB-OFFER |o--|{ JOB-TO-CATEGORIES : maps
    JOB-OFFER ||--|{ CURRENCY : uses
    JOB-OFFER ||--|{ LOCATION : based-in
    JOB-OFFER ||--|{ DATA-SOURCE : sourced-from
    JOB-OFFER |o--|{ EXPERIENCE : requires
    JOB-TO-SKILLS }|--o| SKILL-LIST : includes
    JOB-TO-CATEGORIES }|--o| JOB-CATEGORY : includes
    
    
    JOB-TITLE {
        int jt_id PK
        string name
        string unique_job_title UK
    }

    CURRENCY {
        int c_id PK
        string symbol
        string name
    }

    EXPERIENCE {
        int e_id PK
        string level
        string unique_experience UK
    }

    LOCATION {
        int l_id PK
        string country
        string region
        string city
        string city_district
        string area_code
        string state
        string unique_location_tuple UK
    }

    DATA-SOURCE {
        int ds_id PK
        string name
        string unique_data_source UK
    }

    SKILL-LIST {
        int sl_id PK
        string name
        string unique_skill_name UK
    }

    JOB-CATEGORY {
        int jc_id PK
        string name
        string unique_job_category UK
    }

    JOB-OFFER {
        int jo_id PK
        string source_id
        date published
        int salary_min
        int salary_max
        string joboffer_url
        int job_title_id FK
        int currency_id FK
        int location_id FK
        int data_source_id FK
        int experience_id FK
        string unique_data_source_id UK
        string unique_joboffer UK
    }

    JOB-TO-SKILLS {
        int job_id FK
        int skill_id FK
    }

    JOB-TO-CATEGORIES {
        int job_id FK
        int cat_id FK
    }