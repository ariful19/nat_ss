/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { useCallback, useMemo, ReactNode, useRef } from 'react';
import rison from 'rison';
import {
  t,
  JsonResponse,
  ClientErrorObject,
  getClientErrorObject,
} from '@superset-ui/core';
import { AsyncSelect } from '@superset-ui/core/components';
import { cachedSupersetGet } from 'src/utils/cachedSupersetGet';
import { Dataset, DatasetSelectLabel } from 'src/features/datasets/DatasetSelectLabel';
import { SupersetClient } from '@superset-ui/core';

interface DatasetSelectProps {
  onChange: (value: { label: string; value: number }) => void;
  value?: { label: string; value: number };
}

const DatasetSelect = ({ onChange, value }: DatasetSelectProps) => {
  const getErrorMessage = useCallback(
    ({ error, message }: ClientErrorObject) => {
      let errorText = message || error || t('An error has occurred');
      if (message === 'Forbidden') {
        errorText = t('You do not have permission to edit this dashboard');
      }
      return errorText;
    },
    [],
  );

  // Cache of view labels per dbId|schema to avoid duplicate requests
  const viewLabelsCacheRef = useRef<Record<string, Record<string, string>>>({});

  const loadDatasetOptions = async (
    search: string,
    page: number,
    pageSize: number,
  ) => {
    const query = rison.encode({
      columns: [
        'id',
        'table_name',
        'database.database_name',
        'database.id',
        'schema',
      ],
      filters: [{ col: 'table_name', opr: 'ct', value: search }],
      page,
      page_size: pageSize,
      order_column: 'table_name',
      order_direction: 'asc',
    });
    return cachedSupersetGet({ endpoint: `/api/v1/dataset/?q=${query}` })
      .then(async (response: JsonResponse) => {
        const items: Dataset[] = response.json.result as Dataset[];

        // Gather unique dbId|schema groups to fetch view labels
        const groups = new Map<string, { dbId: number; schema: string }>();
        items.forEach(item => {
          const dbId = (item.database as any)?.id as number | undefined;
          const schema = item.schema;
          if (dbId && schema) {
            const key = `${dbId}|${schema}`;
            if (!groups.has(key)) groups.set(key, { dbId, schema });
          }
        });

        const fetches: Promise<void>[] = [];
        groups.forEach(({ dbId, schema }, key) => {
          if (!viewLabelsCacheRef.current[key]) {
            const endpoint = `/api/v1/database/${dbId}/tables/?q=${rison.encode({
              schema_name: encodeURIComponent(schema),
            })}`;
            fetches.push(
              SupersetClient.get({ endpoint }).then((res: JsonResponse) => {
                const options = res.json.result as Array<{
                  value: string;
                  label?: string;
                  type: string;
                }>;
                const map: Record<string, string> = {};
                options.forEach(opt => {
                  if (opt.label) map[opt.value] = opt.label;
                });
                viewLabelsCacheRef.current[key] = map;
              }),
            );
          }
        });
        if (fetches.length) await Promise.all(fetches);

        const list: {
          label: string | ReactNode;
          value: string | number;
          customLabel?: string;
        }[] = items.map((item: Dataset) => {
          const dbId = (item.database as any)?.id as number | undefined;
          const schema = item.schema;
          const key = dbId && schema ? `${dbId}|${schema}` : undefined;
          const displayName = key
            ? viewLabelsCacheRef.current[key]?.[item.table_name]
            : undefined;
          return {
            label: DatasetSelectLabel(item, displayName),
            value: item.id,
            customLabel: `${displayName || ''} ${item.table_name}`.trim(),
          };
        });

        return {
          data: list,
          totalCount: response.json.count,
        };
      })
      .catch(async error => {
        const errorMessage = getErrorMessage(await getClientErrorObject(error));
        throw new Error(errorMessage);
      });
  };

  return (
    <AsyncSelect
      ariaLabel={t('Dataset')}
      value={value}
      options={loadDatasetOptions}
      optionFilterProps={['value', 'customLabel']}
      onChange={onChange}
      notFoundContent={t('No compatible datasets found')}
      placeholder={t('Select a dataset')}
    />
  );
};

const MemoizedSelect = (props: DatasetSelectProps) =>
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useMemo(() => <DatasetSelect {...props} />, []);

export default MemoizedSelect;
